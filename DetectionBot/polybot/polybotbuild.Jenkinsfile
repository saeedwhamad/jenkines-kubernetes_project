pipeline {
    agent any
    stages{
        stage('Build') {

            steps {
                   sh '''
                    docker login -u saeedwh -p sa22edhama
                    docker image build -t polybotk8s:${BUILD_NUMBER} ./DetectionBot/polybot
                    docker tag polybotk8s:${BUILD_NUMBER} saeedwh/polybotk8s:${BUILD_NUMBER}
                    docker push saeedwh/polybotk8s:${BUILD_NUMBER}
                      '''
                      }
        }
        stage('Trigger Deploy') {
            steps {
                  build job: 'polybotDeploy', wait: false, parameters: [
                      string(name: 'tag_number', value: "${BUILD_NUMBER}")
                           ]
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
