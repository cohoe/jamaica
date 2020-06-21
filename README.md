Jamaica
=======

The API server

Image Build
-----------
```
s2i build -E ./.s2i/environment . centos/python-36-centos7 quay.io/grantcohoe/jamaica
docker push quay.io/grantcohoe/jamaica
oc tag quay.io/grantcohoe/jamaica:latest jamaica:latest
```

One-time
```
oc set image-lookup jamaica
```
