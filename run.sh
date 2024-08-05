#设置PROJECT NAME
export PROJECT_NAME=yproject 
#设置APP NAME
export APP_NAME=nginx-demo
#设置APP NAMESPACE
export APP_NAMESPACE=default
#设置APP_STACK_PATH
export APP_STACK_PATH="organization/$PROJECT_NAME/${APP_NAMESPACE}_${APP_NAME}"
#设置lib目录
export PULUMI_WORKSPACE="${HOME}/pulumi_kustomize_demo"
export PYTHONPATH="$PULUMI_WORKSPACE"
#设置pulumi工作目录,如果pulumi不是使用本地stack，删除这个配置
export PULUMI_HOME="${HOME}/pulumi_home"
mkdir -p ${PULUMI_HOME}/$PROJECT_NAME/${APP_NAMESPACE}_${APP_NAME}
export PULUMI_BACKEND_URL="file:///${PULUMI_HOME}/$PROJECT_NAME/${APP_NAMESPACE}_${APP_NAME}"
export PULUMI_CONFIG_PASSPHRASE="${APP_NAME}"

#设置配置中心VAULT，这里修改为你的vault的配置
export VAULT_ADDR=[VAULT_SERVER_URL] 
export VAULT_TOKEN=[VAULT_TOKEN]  
export APP_CONFIG_PATH="pulumi/data/k8s/test/$PROJECT_NAME/$APP_NAMESPACE/$APP_NAME/config"



#推送应用数据
#vault kv put $APP_CONFIG_PATH @nginx.json
pulumi login --local
cd pulumi/${APP_NAMESPACE}/${APP_NAME}/
pulumi stack select $APP_STACK_PATH || pulumi stack init $APP_STACK_PATH
pulumi config set $PROJECT_NAME:vault_address $VAULT_ADDR
pulumi config set --plaintext $PROJECT_NAME:vault_token $VAULT_TOKEN
pulumi preview --stack $APP_STACK_PATH
#TF_LOG=TRACE pulumi preview --stack $APP_STACK_PATH --logtostderr --logflow -v=10

