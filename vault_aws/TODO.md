### Hashicorp Vault AWS Cloud Template TODO for deploying staging server ###

1. Make sure that the main CloudFormation template (https://github.com/frdr-dfdr/frdr_encryption_client/blob/master/vault_aws/quickstart-hashicorp-vault-main.template.yaml) points to the new FRDR fork of the sub-templates and python scripts at:
https://github.com/frdr-dfdr/cfn-ps-hashicorp-vault

2. Upgrade all Vault, Python, and Ubuntu versions in both the main and nested templates for all applications, lambdas, etc..

3. Add new security group firewall rules to the CloudFormation template once they are decided beyond the home ip addresses of FRDR developers. 
The existing security rules for the main frdrvault.net Load Balancer (https://us-west-2.console.aws.amazon.com/ec2/home?region=us-west-2#LoadBalancer:loadBalancerArn=arn:aws:elasticloadbalancing:us-west-2:975050131716:loadbalancer/app/frdr-v-Vault-s6kXISkOUDwJ/d3184a0b7c34159d;tab=security)
will have to be updated as well.

4. Create the backup s3 bucket in the CloudFormation Template.

5. Make sure that the IAM permissions to read/write/delete on the backup s3 bucket are added to the IAM permission file in the CloudFormation template.

    {
      "Sid": "ListBucketContents",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::frdrvault-backup-bucket"
    },
    {
      "Sid": "ReadWriteBucketObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::frdrvault-backup-bucket/*"
      
(the name of the bucket will need to be unique for each deployment)

6. Add the backup shell script (https://github.com/frdr-dfdr/frdr_encryption_client/blob/master/vault_aws/backup.sh)
   and hourly cron job that runs it into the WebFormation template.

7. After deploying a staging environment, add some test keys into the production frdrvault.net, and then see if you can restore them into
   the staging environment using the backup instructions in the backup script.
    }
  ]
}
