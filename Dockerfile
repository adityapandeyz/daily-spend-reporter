# Use the official AWS Lambda image for Python 3.13
FROM public.ecr.aws/lambda/python:3.13 as builder

# Copy requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies to the target directory
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt -t ${LAMBDA_TASK_ROOT}

# Production stage
FROM public.ecr.aws/lambda/python:3.13

# Copy installed packages from builder
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}/

# Copy application code
COPY main.py models.py schemas.py database.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["main.handler"]
