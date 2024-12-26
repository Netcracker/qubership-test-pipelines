service="$1"
version_var_name=$service"_version"
service_version="${!version_var_name}"
app_var_name=$service"_app_name";
service_app_name="${!app_var_name}";

if [ ${service_version} ]; then
    VERSION=${service_version}
    echo PAY ATTENTION! Version from file!
elif [ $CCI_INTEGRATION = "true" ]; then
  echo CCI integration is enabled, start to get version for $service from CCI ...;
  source ./.env_cci;
  if [ ${!service_app_name} ]; then
    VERSION=${!service_app_name};
  fi
  if [ "$VERSION" = "" ]; then
    echo No version found;
    exit 1;
  fi
else
  echo No version specified;
  exit 1;
fi
echo FINAL $service version $VERSION;
