from unittest.mock import AsyncMagicMixin
from diagrams import Diagram, Cluster

from diagrams.aws.compute import EKS, EC2
from diagrams.aws.network import NLB, Route53, ALB
from diagrams.aws.database import Aurora, ElastiCache
from diagrams.aws.storage import S3
from diagrams.aws.general import Client
from diagrams.onprem.queue import Kafka, ActiveMQ


with Diagram("Finance Pocket Architecture", show=False, direction="TB",
             graph_attr={"pad": "0.5", "nodesep": "0.8", "ranksep": "1.2", "splines": "ortho"},
             node_attr={"shape": "box", "style": "rounded"},
             edge_attr={"arrowsize": "1.5"}):


    nlb = NLB("Load Balancer")

    with Cluster("Services"):
        alb = ALB("Application Load Balancer")
        api = EKS("Backend Service")

        with Cluster("Background"):
            background = EC2("Worker Scheduler")
            mq = ActiveMQ("Message Queue")
            celery = EKS("Background Jobs (Interruptable)")

            background - mq
            mq - celery


    with Cluster("Data Layer"):
        with Cluster("Database", direction="TB"):
            db_primary = Aurora("primary")
            replica = Aurora("replica")
            db_primary - replica

        cache = ElastiCache("Redis")
        kafka = Kafka("Kafka")
        storage = S3("Storage")

    Client("User") >> Route53("DNS") >> nlb >> alb >> api

    api >> kafka >> background

    background >> db_primary
    background >> replica

    api >> db_primary
    api >> cache
    api >> storage
