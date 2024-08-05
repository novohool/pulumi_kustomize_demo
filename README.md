## 使用ubuntu22测试
## 境外服务器（pulumi初始化插件快一些）

#### 说明
- 优势:
- - 服务配置使用vault进行管理，界面配置化
- - 可以结合gitlab进行发布，也可以堡垒机发布
- - 无需在k8s集群添加额外的东西，比如crd，secret，对经常进行k8s进行升级的服务友好
- - pulumi这里使用local,如果生产，建议修改为s3服务或者azure的blob

#### 前提
- vault作为配置中心，需部署vault
- 修改run.sh中的VAULT


#### 其他
- pulumi V2 api估计是为了对标苹果的pkl，有些情况只支持一种数据类型，但yaml支持两种类型，它会自动转换掉，所以这里没有使用v2版本api
- 苹果的pkl地址: https://github.com/apple/pkl-k8s-examples
