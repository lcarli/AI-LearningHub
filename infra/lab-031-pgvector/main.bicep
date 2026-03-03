@description('PostgreSQL server name (must be globally unique)')
param serverName string = 'pgvector-${uniqueString(resourceGroup().id)}'

@description('Administrator login name')
param administratorLogin string = 'pgadmin'

@description('Administrator password')
@secure()
param administratorLoginPassword string

@description('Location for all resources')
param location string = resourceGroup().location

@description('PostgreSQL version')
@allowed(['15', '16'])
param postgresVersion string = '16'

@description('Database name')
param databaseName string = 'ragdb'

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: serverName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    version: postgresVersion
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// Enable pgvector extension
resource pgvectorConfig 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-06-01-preview' = {
  parent: postgresServer
  name: 'azure.extensions'
  properties: {
    value: 'vector'
    source: 'user-override'
  }
}

// Create the RAG database
resource ragDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = {
  parent: postgresServer
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Allow Azure services to connect
resource allowAzureFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-06-01-preview' = {
  parent: postgresServer
  name: 'AllowAllAzureServicesAndResourcesWithinAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

output serverFqdn string = postgresServer.properties.fullyQualifiedDomainName
output connectionString string = 'postgresql://${administratorLogin}@${serverName}:${administratorLoginPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/${databaseName}?sslmode=require'
output serverName string = serverName
