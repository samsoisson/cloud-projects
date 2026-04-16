// Create OpenSearch Service domain for traffic analytics
const openSearchDomain = new opensearch.Domain(this, 'OpenSearchDomain', {
  domainName: props?.domainName || `traffic-analytics-${uniqueSuffix}`,
  version: opensearch.EngineVersion.OPENSEARCH_2_11,
  capacity: {
    dataNodes: 1,
    dataNodeInstanceType: 't3.small.search',
    masterNodes: 0,
  },
  ebs: {
    volumeSize: 20,
    volumeType: cdk.aws_ec2.EbsDeviceVolumeType.GP3,
  },
  nodeToNodeEncryption: true,
  encryptionAtRest: {
    enabled: true,
  },
  enforceHttps: true,
  tlsSecurityPolicy: opensearch.TLSSecurityPolicy.TLS_1_2, // Enforce TLS 1.2 or above
  logging: {
    slowSearchLogEnabled: true,
    appLogEnabled: true,
    slowIndexLogEnabled: true,
  },
  accessPolicies: [
    new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      principals: [new iam.AnyPrincipal()],
      actions: ['es:*'],
      resources: ['*'],
    }),
  ],
  removalPolicy: cdk.RemovalPolicy.DESTROY,
});