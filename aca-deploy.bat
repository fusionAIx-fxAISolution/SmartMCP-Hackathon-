@echo off
setlocal enabledelayedexpansion

REM Variables
set RESOURCE_GROUP=general_dev
set LOCATION=centralindia
set ENVIRONMENT_NAME=general-dev-env
set APP_NAME=pega-mcp
set ACR_NAME=fxdevacr
set IMAGE_TAG=v1.0.6
set IMAGE_NAME=smart-mcp-server
set LOCAL_IMAGE_NAME=%IMAGE_NAME%:%IMAGE_TAG%
set FULLY_QUALIFIED_IMAGE_NAME=%ACR_NAME%.azurecr.io/%IMAGE_NAME%:%IMAGE_TAG%
set IDENTITY_NAME=pega-mcp-identity

REM Login to ACR
az acr login --name %ACR_NAME%

REM Build Docker image
docker buildx build --load --no-cache --platform linux/amd64 -t %LOCAL_IMAGE_NAME% .

REM Tag image
docker tag %LOCAL_IMAGE_NAME% %FULLY_QUALIFIED_IMAGE_NAME%

REM Push image
docker push %FULLY_QUALIFIED_IMAGE_NAME%

REM Get ACR tags
for /f "delims=" %%i in ('az acr repository show-tags --name %ACR_NAME% --repository %IMAGE_NAME% --output tsv') do (
set ACR_TAGS=%%i
)

REM Get Identity IDs
for /f "delims=" %%i in ('az identity show --name %IDENTITY_NAME% --resource-group %RESOURCE_GROUP% --query id -o tsv') do (
set IDENTITY_ID=%%i
)

for /f "delims=" %%i in ('az identity show --name %IDENTITY_NAME% --resource-group %RESOURCE_GROUP% --query principalId -o tsv') do (
set PRINCIPAL_ID=%%i
)

REM ACR Resource Group
set ACR_RESOURCE_GROUP=fxAgentSDK

for /f "delims=" %%i in ('az acr show --name %ACR_NAME% --resource-group %ACR_RESOURCE_GROUP% --query id -o tsv') do (
set ACR_ID=%%i
)

REM Assign role
az role assignment create --assignee %PRINCIPAL_ID% --scope %ACR_ID% --role acrpull

REM Create Container App Environment
az containerapp env create ^
--name %ENVIRONMENT_NAME% ^
--resource-group %RESOURCE_GROUP% ^
--location %LOCATION%

REM Create Container App and capture FQDN
for /f "delims=" %%i in ('az containerapp create ^
--name %APP_NAME% ^
--resource-group %RESOURCE_GROUP% ^
--environment %ENVIRONMENT_NAME% ^
--image %FULLY_QUALIFIED_IMAGE_NAME% ^
--registry-server %ACR_NAME%.azurecr.io ^
--registry-identity %IDENTITY_ID% ^
--user-assigned %IDENTITY_ID% ^
--target-port 8000 ^
--ingress external ^
--env-vars REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt BASE_URL=%BASE_URL% API_KEY=%API_KEY% ^
--min-replicas 1 ^
--max-replicas 3 ^
--cpu 1 ^
--memory 2Gi ^
--query properties.configuration.ingress.fqdn -o tsv') do (
set FQDN=%%i
)

echo App URL: %FQDN%

REM Update scaling rules
  

endlocal
