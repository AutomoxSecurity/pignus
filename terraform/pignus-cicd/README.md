<img width="700" alt="Automox" src="https://cdn2.hubspot.net/hubfs/2242551/+Logos/automox-trademark-blue.png">

# Pignus CICD
Continuous development for the [Pignus](https://github.com/PatchSimple/pignus) repository.

## Processes
### [Pipeline] Pignus Development
 - Run [unit tests](https://github.com/PatchSimple/pignus/tree/main/tests/unit) locally.
 - Create the Docker image
 - Deploy Docker image to Pignus-Gateway and Pignus-Sentry Lambdas
 - Run [regression tests](https://github.com/PatchSimple/pignus/tree/main/tests/regression)

## Setup
@todo



## Rolling a new database
### Steps for a new database
    - Set new database name in [Pignus Api SecOps vars](https://github.com/PatchSimple/pignus/tree/main/terraform/pignus-api/vars/secops.tfvars)
    - Apply Pignus Api terraform with new database name
    - Run Lambda Pignus-Sentry with the migrations option.
    - Get api-key for pignus-admin.
    - Use that api-key to create 3 new users with [Example: Create Users](https://github.com/PatchSimple/pignus/tree/main/examples/pignus-api/create_user.py)
        - User `test_regression` and place the api key in the AWS SSM parameter `PIGNUS_API_KEY_DEV_ROLE_ADMIN`
        - User `test_cluster_user` and place the api key in the AWS SSM parameter `PIGNUS_API_KEY_DEV_ROLE_CLUSTER`
        - User `secops_cluster` and place those credentials in the secops cluster configmap. 
          ```
          echo "the-key" | base64
          kubectl -n secops edit secret pignus-api
          ```
