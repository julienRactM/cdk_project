import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_app7.cdk_app7_stack import CdkApp7Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_app7/cdk_app7_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkApp7Stack(app, "cdk-app7")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
