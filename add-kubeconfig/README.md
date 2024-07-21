```
sudo rm -rf /bin/add-kubeconfig && sudo cp add-kubeconfig.py /bin/add-kubeconfig && sudo chmod +x /bin/add-kubeconfig
```

```
qtu100@qtu100:~/dev/avant/MAIN/1-COMMON/OTHER/common.scripts/add-kubeconfig$ add-kubeconfig admin.yaml
Hi! I'm utility that can take one kubeconfig and merge it's content with another kubeconfig!
Your kubeconfig points to localhost! It is likely that it would not work! Proceed anyway? (y/N): 
Operation canceled
```

```
qtu100@qtu100:~/dev/avant/MAIN/1-COMMON/OTHER/common.scripts/add-kubeconfig$ add-kubeconfig admin.yaml
Hi! I'm utility that can take one kubeconfig and merge it's content with another kubeconfig!
We will merge data from admin.yaml into /home/qtu100/.kube/config. Is that ok? (Y/n): 
How would we name the cluster (existing cluster with the same name will be overwritten)?: dev-hss-v1
All done!
```
