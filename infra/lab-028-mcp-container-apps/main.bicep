@description('Base name for all resources (lowercase letters and numbers only)')
param baseName string = 'mcp${uniqueString(resourceGroup().id)}'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Container image for the MCP server (use mcr.microsoft.com/azuredocs/containerapps-helloworld:latest to test)')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('MCP server port')
param containerPort int = 8000

var logAnalyticsName = 'log-${baseName}'
var environmentName = 'cae-${baseName}'
var appName = 'mcp-server-${baseName}'

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource mcpServerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: containerPort
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
    }
    template: {
      containers: [
        {
          name: 'mcp-server'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'PORT'
              value: string(containerPort)
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}

output appUrl string = 'https://${mcpServerApp.properties.configuration.ingress.fqdn}'
output appName string = appName
output environmentName string = environmentName
output resourceGroup string = resourceGroup().name
