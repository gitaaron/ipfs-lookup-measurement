output "monitor_ip" {
  description = "Public IP address of monitor"
  value       = aws_instance.ipfs_testing_monitor.public_ip
}

output "node_0_ip" {
  description = "Public IP address of node 0"
  value       = module.testing_node_0.public_ip
}

output "node_1_ip" {
  description = "Public IP address of node 1"
  value       = module.testing_node_1.public_ip
}

output "node_2_ip" {
  description = "Public IP address of node 2"
  value       = module.testing_node_2.public_ip
}

output "node_3_ip" {
  description = "Public IP address of node 3"
  value       = module.testing_node_3.public_ip
}

output "node_4_ip" {
  description = "Public IP address of node 4"
  value       = module.testing_node_4.public_ip
}

output "node_5_ip" {
  description = "Public IP address of node 5"
  value       = module.testing_node_5.public_ip
}
