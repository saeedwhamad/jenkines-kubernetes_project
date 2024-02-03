pipeline {
    agent any

    parameters {
     string(name: 'tag_number', defaultValue: 'latest', description: 'Docker image tag')
     }

    stages {
        stage('Deploy') {
            steps {

                  script {
                    sh "export TAG=${tag_number} && envsubst < /k8s/yolo5deployment.yaml | kubectl apply -f -"
                }
            }
        }
    }
}