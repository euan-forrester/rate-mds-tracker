# high-five-tracker

Fraser Health has a system where patients can leave nice messages called High Fives thanking staff for the care they received: https://www.fraserhealth.ca/highfive

This system is curated and updated periodically by hand. The only issue is that staff members aren't notified when they are the subject of a High Five.

This system runs daily in AWS Lambda and watches for new High Fives and sees if any contain strings matching a list of names provided, and if so sends an email containing those High Fives to the email address provided.

![Example High Five email](https://github.com/euan-forrester/high-five-tracker/raw/main/images/example-email.png "Example High Five email")

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

Log into your docker repository:

```
eval "$(aws ecr get-login --no-include-email --region us-west-2)"
```

Then build and push your image:

```
cd src
docker build -f ./Dockerfile .
docker images
docker tag <ID of image you just built> <URI of high-five-tracker-[dev|prod] repository in ECR: use AWS console to find>
docker push <URI of high-five-tracker-[dev|prod] repository in ECR>
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
