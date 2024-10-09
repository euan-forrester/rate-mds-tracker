# rate-mds-tracker

RateMDs.com is a website where patients can leave reviews for physicians. Most reviews are quite nice. 

This system runs daily in AWS Lambda and watches for new ratings above a certain score threshold, and if so sends an email containing those reviewss to the email address provided.

![Example email](https://github.com/euan-forrester/rate-mds-tracker/raw/main/images/example-email.png "Example email")

### Setup

#### Step 0: Configure `terraform.tfvars`

Copy `terraform/terraform.tfvars.example` to `terraform/[dev|prod]/.terraform/terraform.tfvars`

Fill in the search strings, communities, email addresses, and any other information needed.

Note that setting the communities restricts searching for names within those communities only, to cut down on the number of false positives for common names.

#### Step 1: Initial terraform

This sets up most of the AWS infrastructure, and in particular sets up an ECR repository to hold the Docker image of our Lambda function.

Note that this will end in an error because the ECR repository is empty

```
cd terraform/[dev|prod]
terraform init
terraform apply
```

#### Step 2: Push docker image to ECR

Install docker: https://docs.docker.com/install/

Install the AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-bundle.html

Note that you need to create & populate `~/.aws/credentials`. There is an example in `terraform/aws_credentials.example`

These instructions are also found on the AWS ECR page, by clicking on the repository and then "View push commands"

Log into your docker repository:

```
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <aws account id>.dkr.ecr.us-west-2.amazonaws.com
```

Then build and push your image:

```
cd src
docker build -t rate-mds-tracker-[dev|prod] . --provenance=false
docker tag rate-mds-tracker-[dev|prod]:latest <aws account id>.dkr.ecr.us-west-2.amazonaws.com/rate-mds-tracker-[dev|prod]:latest
docker push <aws account id>.dkr.ecr.us-west-2.amazonaws.com/rate-mds-tracker-[dev|prod]:latest
```

#### Step 3: Run terraform again

With the ECR repository now containing an image for our Lambda function, re-run

```
terraform apply
```

again from the appropriate directory to finish setting up our AWS infrastruture


### Run tests

```
pip3 install -U pytest
cd tests
pytest
```
