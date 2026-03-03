@description('Prefix for all resource names')
param prefix string = 'ailab'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Your Azure AD user object ID (used to assign AI Developer role)')
param userObjectId string = ''

var aiHubName = '${prefix}-hub-${uniqueString(resourceGroup().id)}'
var aiProjectName = '${prefix}-project'
var storageName = '${prefix}st${uniqueString(resourceGroup().id)}'
var keyVaultName = '${prefix}-kv-${uniqueString(resourceGroup().id)}'

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    accessPolicies: []
  }
}

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-01-01-preview' = {
  name: aiHubName
  location: location
  kind: 'Hub'
  identity: { type: 'SystemAssigned' }
  properties: {
    storageAccount: storage.id
    keyVault: keyVault.id
    friendlyName: 'AI Agents Learning Hub'
    description: 'Azure AI Foundry Hub for Lab 030'
  }
}

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-01-01-preview' = {
  name: aiProjectName
  location: location
  kind: 'Project'
  identity: { type: 'SystemAssigned' }
  properties: {
    hubResourceId: aiHub.id
    friendlyName: 'Outdoor Gear Agent Project'
    description: 'AI project for building the OutdoorGear customer service agent'
  }
}

// Assign AI Developer role to the deploying user (optional)
var aiDeveloperRoleId = '64702f94-c441-49e6-a78b-ef80e0188fee'
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(userObjectId)) {
  name: guid(aiProject.id, userObjectId, aiDeveloperRoleId)
  scope: aiProject
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', aiDeveloperRoleId)
    principalId: userObjectId
    principalType: 'User'
  }
}

output hubName string = aiHubName
output projectName string = aiProjectName
output projectUrl string = 'https://ai.azure.com/build/${aiProject.id}'
output resourceGroup string = resourceGroup().name
