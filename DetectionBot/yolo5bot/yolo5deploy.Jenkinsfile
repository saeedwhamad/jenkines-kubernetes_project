pipeline {
    agent any

    parameters {
     string(name: 'tag_number', defaultValue: 'latest', description: 'Docker image tag')
     }

    stages {
        stage('Deploy') {
            steps {

                 sh "kubectl apply -f /k8s/yolo5deployment.yaml --env=TAG=${tag_number}"
            }
        }
    }
}