role.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: [
    'ssm:*',
    'ec2:*',
    'rds:*',
    's3:*',
    'lambda:*',
    'states:*',
    'events:*',
    'cloudwatch:*',
    'sns:*',
    'logs:*',
    'backup:*',
    // 'iam:PassRole' removed for least privilege
  ],
  resources: ['*']
}));

// Add a restricted PassRole statement for only the automation role itself
// Moved write permission from workflow level to job level as per vulnerability fix
// The following block has been removed to address the vulnerability:
// role.addToPolicy(new iam.PolicyStatement({
//   effect: iam.Effect.ALLOW,
//   actions: [
//     'iam:PassRole'
//   ],
//   resources: [role.roleArn]
// }));

// When accessing S3 buckets, ensure the 'ExpectedBucketOwner' parameter is used to verify bucket ownership
// Example usage with AWS SDK for JavaScript v3:
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";

const s3Client = new S3Client({ region: "us-east-1" });

async function getObjectFromBucket(bucketName, key, expectedBucketOwner) {
  const command = new GetObjectCommand({
    Bucket: bucketName,
    Key: key,
    ExpectedBucketOwner: expectedBucketOwner, // Added for ownership verification
  });
  return await s3Client.send(command);
}

// Usage:
// await getObjectFromBucket('my-bucket', 'my-key', '123456789012');