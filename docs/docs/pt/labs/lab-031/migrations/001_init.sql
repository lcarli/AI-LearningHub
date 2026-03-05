-- =============================================================================
-- Migration 001: Initialize OutdoorGear pgvector Schema
-- Lab 031: pgvector Semantic Search with Azure PostgreSQL
-- =============================================================================
-- Run this against an Azure Database for PostgreSQL Flexible Server
-- with the pgvector extension enabled.
-- =============================================================================

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for optional keyword search fallback
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =============================================================================
-- PRODUCTS table
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id            TEXT PRIMARY KEY,          -- e.g. 'P001'
    name          TEXT NOT NULL,
    category      TEXT NOT NULL,             -- 'tents', 'sleeping_bags', 'backpacks', 'clothing', 'footwear'
    description   TEXT NOT NULL,
    price_usd     NUMERIC(10, 2),
    weight_grams  INTEGER,
    in_stock      BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- PRODUCT EMBEDDINGS table
-- =============================================================================
-- Stores the vector embedding for each product.
-- Separated from products table so embeddings can be regenerated independently.
-- Using 1536 dimensions for text-embedding-3-small (Azure OpenAI / GitHub Models).
CREATE TABLE IF NOT EXISTS product_embeddings (
    product_id    TEXT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    embedding     vector(1536) NOT NULL,     -- text-embedding-3-small output dimension
    model_name    TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    embedded_at   TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CUSTOMER QUERIES LOG (optional, for analytics)
-- =============================================================================
CREATE TABLE IF NOT EXISTS search_queries (
    id            BIGSERIAL PRIMARY KEY,
    query_text    TEXT NOT NULL,
    query_embedding vector(1536),
    top_result_id TEXT REFERENCES products(id),
    similarity_score FLOAT,
    searched_at   TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES for vector similarity search
-- =============================================================================

-- IVFFlat index: fast approximate nearest-neighbor search
-- lists = sqrt(row_count) is a good starting point
-- Use for datasets > 10,000 rows. For small datasets, sequential scan is fine.
CREATE INDEX IF NOT EXISTS idx_product_embeddings_ivfflat
    ON product_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- Optional: HNSW index (better recall, more memory)
-- Requires pgvector >= 0.5.0
-- CREATE INDEX IF NOT EXISTS idx_product_embeddings_hnsw
--     ON product_embeddings
--     USING hnsw (embedding vector_cosine_ops)
--     WITH (m = 16, ef_construction = 64);

-- Index for keyword search fallback
CREATE INDEX IF NOT EXISTS idx_products_description_trgm
    ON products
    USING gin (description gin_trgm_ops);

-- Index for category filtering
CREATE INDEX IF NOT EXISTS idx_products_category
    ON products (category);

-- =============================================================================
-- SEED DATA: OutdoorGear Product Catalog
-- =============================================================================
INSERT INTO products (id, name, category, description, price_usd, weight_grams, in_stock)
VALUES
    ('P001', 'TrailBlazer Tent 2P',       'tents',
     'Lightweight 2-person backpacking tent, 3-season, aluminum poles, 2000mm waterproof rating, freestanding design, packed size 15x45cm',
     249.99, 1800, TRUE),

    ('P002', 'Summit Dome 4P',            'tents',
     '4-season expedition tent for 4 people, steel poles, snow load rated, vestibule entry, extreme weather tested, double-wall construction',
     549.99, 3200, TRUE),

    ('P003', 'TrailBlazer Solo',          'tents',
     'Ultra-light solo tent, 3-season, single-wall design, freestanding, ideal for fast-and-light backpacking, carbon fiber pole option available',
     299.99, 850, TRUE),

    ('P004', 'ArcticDown -20°C Bag',      'sleeping_bags',
     'Winter sleeping bag with 800-fill power responsibly sourced down, rated to -20°C, mummy shape, draft collar, YKK zipper, water-resistant shell',
     389.99, 1400, TRUE),

    ('P005', 'SummerLight +5°C Bag',      'sleeping_bags',
     'Lightweight summer sleeping bag, synthetic insulation rated to +5°C, side zipper for ventilation, quick-drying, stuff sack included',
     149.99, 700, TRUE),

    ('P006', 'Osprey Atmos 65L',          'backpacks',
     '65-liter backpacking pack with anti-gravity suspension system, hipbelt pockets, hydration sleeve compatible, fits torso 40-52cm, rain cover included',
     289.99, 1980, TRUE),

    ('P007', 'DayHiker 22L',              'backpacks',
     '22-liter lightweight daypack, padded laptop sleeve 15-inch, hydration compatible, multiple pockets, sternum strap, reflective accents',
     89.99, 580, TRUE)

ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- HELPER FUNCTION: cosine similarity search
-- =============================================================================
-- Usage: SELECT * FROM search_products_by_vector('[0.1, 0.2, ...]'::vector, 5, 0.5);
CREATE OR REPLACE FUNCTION search_products_by_vector(
    query_vector  vector(1536),
    max_results   INTEGER DEFAULT 5,
    min_similarity FLOAT DEFAULT 0.3
)
RETURNS TABLE (
    product_id    TEXT,
    name          TEXT,
    category      TEXT,
    description   TEXT,
    price_usd     NUMERIC(10,2),
    similarity    FLOAT
)
LANGUAGE sql STABLE AS $$
    SELECT
        p.id,
        p.name,
        p.category,
        p.description,
        p.price_usd,
        1 - (pe.embedding <=> query_vector) AS similarity
    FROM product_embeddings pe
    JOIN products p ON p.id = pe.product_id
    WHERE p.in_stock = TRUE
      AND 1 - (pe.embedding <=> query_vector) >= min_similarity
    ORDER BY pe.embedding <=> query_vector   -- operator: cosine distance (smaller = more similar)
    LIMIT max_results;
$$;

-- =============================================================================
-- HELPER VIEW: products with embedding status
-- =============================================================================
CREATE OR REPLACE VIEW v_product_embedding_status AS
    SELECT
        p.id,
        p.name,
        p.category,
        p.in_stock,
        CASE WHEN pe.product_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_embedding,
        pe.embedded_at,
        pe.model_name
    FROM products p
    LEFT JOIN product_embeddings pe ON pe.product_id = p.id;

-- Verify setup
SELECT 'Migration 001 complete' AS status;
SELECT * FROM v_product_embedding_status;
