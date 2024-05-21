"""
 Copyright 2024 Adobe
 All Rights Reserved.

 NOTICE: Adobe permits you to use, modify, and distribute this file in
 accordance with the terms of the Adobe license agreement accompanying it.
"""

import logging
import os
from datetime import datetime

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.config.client_config import ClientConfig
from adobe.pdfservices.operation.config.proxy.proxy_scheme import ProxyScheme
from adobe.pdfservices.operation.config.proxy.proxy_server_config import ProxyServerConfig
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.create_pdf_job import CreatePDFJob
from adobe.pdfservices.operation.pdfjobs.result.create_pdf_result import CreatePDFResult

# Initialize the logger
logging.basicConfig(level=logging.INFO)


#
# This sample illustrates how to setup Proxy Server configurations for performing an operation. This enables the
# clients to set proxy server configurations to enable the API calls in a network where calls are blocked unless they
# are routed via Proxy server.
#
# Refer to README.md for instructions on how to run the samples.
#
class CreatePDFWithProxyServer:
    def __init__(self):
        try:
            file = open('src/resources/createPDFInput.docx', 'rb')
            input_stream = file.read()
            file.close()

            # Initial setup, create credentials instance
            credentials: ServicePrincipalCredentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )

            # Initial setup, creates proxy server config instance for client config.
            # Replace the values of PROXY_HOSTNAME with the proxy server hostname.
            # If the scheme of proxy server is not HTTP then, replace ProxyScheme parameter with HTTPS.
            # If the port for proxy server is diff than the default port for HTTP and HTTPS, then please set the
            # PROXY_PORT,
            # else, remove its setter statement.
            proxy_server_config: ProxyServerConfig = ProxyServerConfig(
                host="PROXY_HOSTNAME",
                scheme=ProxyScheme.HTTP,
                port=443,
            )

            # Creates client config instance
            client_config: ClientConfig = ClientConfig(
                connect_timeout=10000,
                read_timeout=40000,
                proxy_server_config=proxy_server_config,
            )

            # Creates a PDF Services instance
            pdf_services = PDFServices(
                credentials=credentials,
                client_config=client_config,
            )

            # Creates an asset(s) from source file(s) and upload
            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.DOCX)

            # Creates a new job instance
            create_pdf_job = CreatePDFJob(input_asset)

            # Submit the job and gets the job result
            location = pdf_services.submit(create_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, CreatePDFResult)

            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            # Creates an output stream and copy stream asset's content to it
            output_file_path = self.create_output_file_path()
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())

        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logging.exception(f'Exception encountered while executing operation: {e}')

    # Generates a string containing a directory structure and file name for the output file
    @staticmethod
    def create_output_file_path() -> str:
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        os.makedirs("output/CreatePDFWithProxyServer", exist_ok=True)
        return f"output/CreatePDFWithProxyServer/create{time_stamp}.pdf"


if __name__ == "__main__":
    CreatePDFWithProxyServer()
