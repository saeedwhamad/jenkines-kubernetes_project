pipeline {
    agent any
    stages{
        stage('Build') {
            steps {

                   sh '''
                    docker login -u saeedwh -p sa22edhama
                    docker image build -t yolok8s:${BUILD_NUMBER} ./DetectionBot/yolo5bot
                    docker tag yolok8s:${BUILD_NUMBER} saeedwh/yolok8s:${BUILD_NUMBER}
                    docker push saeedwh/yolok8s:${BUILD_NUMBER}
                      '''
            }

        }
        stage('Deploy to Kubernetes') {
            steps {
            """
                script {
                    // Set Kubeconfig
                    withCredentials([file(credentialsId: 'your_kubeconfig_secret_id', variable: 'KUBECONFIG_FILE')]) {
                        sh "kubectl config view --flatten > ${env.WORKSPACE}/kubeconfig"
                        sh "KUBECONFIG=${env.WORKSPACE}/kubeconfig kubectl apply -f k8s/deployment.yaml --namespace=${K8S_NAMESPACE}"
                    }
                    """
                }
            }
        }

     }
     post {
        success {
            echo 'Docker image built, pushed, and deployed successfully!'
        }

        failure {

            echo 'Docker image build, push, or deploy failed.'
        }
    }
}
