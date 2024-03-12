## How to install and configure a Hashicorp Vault stack on AWS using CloudFormation ##

This directory contains a AWS CloudFormation template to install a 'production hardened' open-source licensed Hashicorp Vault installation and instructions on how to how to correctly use it.

### Resources ###


[General Deployment Guide for Vault CloudFormation Template](https://aws-ia.github.io/cfn-ps-hashicorp-vault/) (Use as reference, not completely accurate)


Github Repository for Hashicorp CloudFormation Templates:

https://github.com/aws-ia/cfn-ps-hashicorp-vault

### Pre-deployment steps ###

1. Create a [ssh EC2 key-pair](https://us-west-2.console.aws.amazon.com/ec2/home?region=us-west-2#KeyPairs) in the us-west-2 (Oregon) zone. (This template is pre-configured to only use us-west-2). Switch zones in the top right-hand corner of your web console.


2. Create a domain name and 'hosted zone' (DNS entry) for the hostname the vault instance will live at (currently: frdrvault.org). Use the [Amazon Route 53 Console](https://us-east-1.console.aws.amazon.com/route53/v2/home?region=us-east-1#Dashboard) to do so. Note: a registration cost is applied here.


3. Create a SSL certificate for your domain name using the [Amazon SSL Cert Manager](https://us-west-2.console.aws.amazon.com/acm/home?region=us-west-2#/certificates/list)


### Deployment ###

1. Go to the [CloudFormation stack creation dashboard](https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create)

2. Select the 'Upload a template file' option and use the [template](./quickstart-hashicorp-vault-main.template.yaml) from this repository.

For user-defined parameters:

Stack Name: frdr-current date

Availability Zones: Pick 3

Permitted IP Range: 0.0.0.0/0 (Users will be coming from arbitrary ip ranges)

KeyPair: Your us-west-2 keypair should be in the dropdown list.

Kubernetes Host Url/Kubernetes CA Certificate/Kubernetes JWT Token: Leave blank.

Internal/External Load Balancer: External

Load Balancer DNS Name: The hostname you picked.

Hosted Zone Id: Leave blank.

SSL Certificate ARN: Get ARN from the SSL certificate manager for the certificate you created for this domain (starts with arn:)

3. Click through until the stack starts deploying, you will be auto-forwarded to the CloudFormation console. Note: this will start billable use of EC2 instances and network egress.

4. If the stack creation succeeds, you will have to associate a hosted zone (DNS) 'A' record with the load balancer created by the stack (the stack is supposed to do this but doesn't appear to work). Follow the steps in [this guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-elb-load-balancer.html) to assign the DNS hostname correctly.

5. Login to Vault instance at your domain, the root key can be accessed from your [AWS Secrets Store](https://us-west-2.console.aws.amazon.com/secretsmanager/listsecrets?region=us-west-2). No more basic configuration is necessary as the Vault is auto-unsealed as part of the deployment.

 
