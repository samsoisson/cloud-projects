@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Environment name (e.g., dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Unique suffix for resource names to ensure global uniqueness')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('App Service Plan SKU')
@allowed(['F1', 'B1', 'B2', 'S1', 'S2', 'P1v2', 'P2v2'])
param appServicePlanSku string = 'B1'

@description('Node.js runtime version for the web app')
@allowed(['NODE:18-lts', 'NODE:20-lts'])
param nodeVersion string = 'NODE:18-lts'

@description('Sample database connection string (for demo purposes)')
@secure()
param databaseConnectionString string

@description('Sample external API key (for demo purposes)')
@secure()
param externalApiKey string

@description('Tags to apply to all resources')
param tags object = {
  purpose: 'secrets-demo'
  environment: environment
  recipe: 'simple-secrets-management'
}

var keyVaultName = 'kv-secrets-${uniqueSuffix}'
var appServicePlanName = 'asp-secrets-${uniqueSuffix}'
var webAppName = 'webapp-secrets-${uniqueSuffix}'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    publicNetworkAccess: 'Enabled'
  }
}

resource databaseConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'DatabaseConnection'
  properties: {
    value: databaseConnectionString
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
}

resource externalApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'ExternalApiKey'
  properties: {
    value: externalApiKey
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
}

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  sku: {
    name: appServicePlanSku
    tier: appServicePlanSku == 'F1' ? 'Free' : appServicePlanSku == 'B1' || appServicePlanSku == 'B2' ? 'Basic' : 'Standard'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  tags: tags
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: nodeVersion
      alwaysOn: appServicePlanSku != 'F1' 
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      appSettings: [
        {
          name: 'DATABASE_CONNECTION'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=DatabaseConnection)'
        }
        {
          name: 'API_KEY'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=ExternalApiKey)'
        }
        {
          name: 'WEBSITE_NODE_DEFAULT_VERSION'
          value: '18-lts'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: subscription()
  name: '4633458b-17de-408a-b874-0445c86b69e6' 
}

resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, webApp.id, keyVaultSecretsUserRole.id)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole.id
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'ai-${webAppName}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-${webAppName}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource webAppInsightsConfig 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: webApp
  name: 'appsettings'
  properties: {
    DATABASE_CONNECTION: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=DatabaseConnection)'
    API_KEY: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=ExternalApiKey)'
    WEBSITE_NODE_DEFAULT_VERSION: '18-lts'
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    APPINSIGHTS_INSTRUMENTATIONKEY: applicationInsights.properties.InstrumentationKey
    APPLICATIONINSIGHTS_CONNECTION_STRING: applicationInsights.properties.ConnectionString
    ApplicationInsightsAgent_EXTENSION_VERSION: '~3'
    XDT_MicrosoftApplicationInsights_Mode: 'Recommended'
  }
  dependsOn: [
    keyVaultRoleAssignment
  ]
}

@description('The name of the created Key Vault')
output keyVaultName string = keyVault.name

@description('The resource ID of the Key Vault')
output keyVaultResourceId string = keyVault.id

@description('The name of the created web app')
output webAppName string = webApp.name

@description('The default hostname of the web app')
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'

@description('The principal ID of the web app managed identity')
output webAppManagedIdentityPrincipalId string = webApp.identity.principalId

@description('The name of the App Service Plan')
output appServicePlanName string = appServicePlan.name

@description('Application Insights Instrumentation Key')
output applicationInsightsInstrumentationKey string = applicationInsights.properties.InstrumentationKey

@description('Application Insights Connection String')
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString

@description('Resource Group Name')
output resourceGroupName string = resourceGroup().name

@description('Deployment Summary')
output deploymentSummary object = {
  keyVault: {
    name: keyVault.name
    resourceId: keyVault.id
  }
  webApp: {
    name: webApp.name
    url: 'https://${webApp.properties.defaultHostName}'
    managedIdentityPrincipalId: webApp.identity.principalId
  }
  appServicePlan: {
    name: appServicePlan.name
    sku: appServicePlanSku
  }
  monitoring: {
    applicationInsights: applicationInsights.name
    logAnalytics: logAnalyticsWorkspace.name
  }
}