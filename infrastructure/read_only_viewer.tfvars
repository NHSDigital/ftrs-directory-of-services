s3_versioning = {
  status     = true
  mfa_delete = false
}
read_only_viewer_bucket_name      = "read-only-viewer-bucket"
read_only_viewer_cloud_front_name = "read-only-viewer-cf"
read_only_viewer_waf_name         = "read-only-viewer-waf-web-acl"
read_only_viewer_ip_set_name      = "read-only-viewer-waf-ip-set"
read_only_viewer_waf_scope        = "CLOUDFRONT"
