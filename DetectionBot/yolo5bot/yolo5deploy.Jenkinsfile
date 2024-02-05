pipeline {
    agent any

    parameters {
     string(name: 'tag_number', defaultValue: '20', description: 'Docker image tag')
     }

    stages {
        stage('Deploy') {
            steps {
                script {
                    withCredentials([aws(credentialsId: AWS_CRED, accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                        sh 'aws eks update-kubeconfig --region us-east-1 --name k8s-main'

                            sh "sed -i 's|image: saeedwh/polybotk8s:.*|image: saeedwh/polybotk8s:${tag_number}|' /k8s/yolo5deployment.yaml"
                            sh 'kubectl apply -f /k8s/yolo5deployment.yaml
'

                    }
                }
            }
        }

    }
}