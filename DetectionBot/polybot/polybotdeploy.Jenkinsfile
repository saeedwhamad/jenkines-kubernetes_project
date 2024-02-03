pipeline {
    agent any

    string(name: 'tag_number', defaultValue: 'latest', description: 'Docker image tag')
    }

    stages {
        stage('Deploy') {
            steps {
                 sh "kubectl apply -f k8s\polybot_pod.yaml --TAG=${tag_number}"
            }
        }
    }
}