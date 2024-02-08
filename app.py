#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_app7.cdk_app7_stack import CdkApp7Stack


env_EU = cdk.Environment(account="944187825807", region="eu-west-3")
env_US = cdk.Environment(account="944187825807", region="us-east-1")

app = cdk.App()
CdkApp7Stack(app, "CdkApp7StackV8", env=env_EU)

app.synth()
