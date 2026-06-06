from flask import Flask, render_template, jsonify
from kubernetes import client, config
import os

app = Flask(__name__)

def init_k8s():
    """Initialize Kubernetes client"""
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

def analyze_cluster():
    """Collect cluster details and identify issues"""
    init_k8s()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()
    
    issues = []
    cluster_info = {}
    
    # Get nodes
    nodes = v1.list_node()
    cluster_info['nodes'] = []
    for node in nodes.items:
        node_info = {
            'name': node.metadata.name,
            'status': 'Ready' if any(c.type == 'Ready' and c.status == 'True' for c in node.status.conditions) else 'NotReady',
            'cpu': node.status.capacity.get('cpu'),
            'memory': node.status.capacity.get('memory')
        }
        cluster_info['nodes'].append(node_info)
        
        if node_info['status'] == 'NotReady':
            issues.append({'severity': 'critical', 'resource': 'Node', 'name': node_info['name'], 'issue': 'Node is not ready'})
    
    # Get pods
    pods = v1.list_pod_for_all_namespaces()
    cluster_info['pods'] = []
    for pod in pods.items:
        pod_info = {
            'name': pod.metadata.name,
            'namespace': pod.metadata.namespace,
            'status': pod.status.phase,
            'restarts': sum(cs.restart_count for cs in pod.status.container_statuses) if pod.status.container_statuses else 0
        }
        cluster_info['pods'].append(pod_info)
        
        if pod_info['status'] not in ['Running', 'Succeeded']:
            issues.append({'severity': 'warning', 'resource': 'Pod', 'name': f"{pod_info['namespace']}/{pod_info['name']}", 'issue': f"Pod status: {pod_info['status']}"})
        
        if pod_info['restarts'] > 5:
            issues.append({'severity': 'warning', 'resource': 'Pod', 'name': f"{pod_info['namespace']}/{pod_info['name']}", 'issue': f"High restart count: {pod_info['restarts']}"})
    
    # Get deployments
    deployments = apps_v1.list_deployment_for_all_namespaces()
    cluster_info['deployments'] = []
    for dep in deployments.items:
        dep_info = {
            'name': dep.metadata.name,
            'namespace': dep.metadata.namespace,
            'replicas': dep.spec.replicas,
            'available': dep.status.available_replicas or 0
        }
        cluster_info['deployments'].append(dep_info)
        
        if dep_info['available'] < dep_info['replicas']:
            issues.append({'severity': 'warning', 'resource': 'Deployment', 'name': f"{dep_info['namespace']}/{dep_info['name']}", 'issue': f"Only {dep_info['available']}/{dep_info['replicas']} replicas available"})
    
    return cluster_info, issues

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cluster')
def get_cluster_data():
    try:
        cluster_info, issues = analyze_cluster()
        return jsonify({'cluster': cluster_info, 'issues': issues})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
