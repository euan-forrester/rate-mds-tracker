# See here for info about how to create an image for AWS Lambda:
# https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-create

FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.9

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN  pip3 install -r requirements.txt

RUN mkdir -p ${LAMBDA_TASK_ROOT}/common

# Copy function code
COPY high-five.py ${LAMBDA_TASK_ROOT}
COPY highfiveparser.py ${LAMBDA_TASK_ROOT}
COPY common/confighelper.py ${LAMBDA_TASK_ROOT}/common/
COPY common/metricshelper.py ${LAMBDA_TASK_ROOT}/common/
COPY common/emailhelper.py ${LAMBDA_TASK_ROOT}/common/

RUN chmod +x ${LAMBDA_TASK_ROOT}/high-five.py

CMD [ "high-five.get_new_high_fives_and_send_email" ]
