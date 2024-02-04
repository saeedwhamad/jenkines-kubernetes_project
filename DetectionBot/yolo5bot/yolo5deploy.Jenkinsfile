pipeline {
    agent any

    parameters {
     string(name: 'tag_number', defaultValue: 'latest', description: 'Docker image tag')
     }

    stages {
        stage('Deploy') {
            steps {

              sh """
              aws eks --region us-east-1 update-kubeconfig --name k8s-main

              kubectl apply -f ./k8s/yolo5deployment.yaml --namespace saeed
               """
            }
        }
    }
}