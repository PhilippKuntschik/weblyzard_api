package com.weblyzard.api.client.integration;

import java.io.IOException;
import java.net.Socket;
import java.util.logging.Logger;
import com.weblyzard.api.client.BasicClient;

public class TestClientBase {

    protected Logger logger = Logger.getLogger(getClass().getName());

    /**
     * Checks if a network service is running.
     *
     * @param host host the server is running on
     * @param port port the server is listening on
     * @return
     */
    public boolean weblyzardServiceAvailable(BasicClient basicClient) {

        String host = basicClient.getBaseTarget().getUri().getHost();
        int port = basicClient.getBaseTarget().getUri().getPort();

        try (Socket s = new Socket(host, port)) {
            return true;
        } catch (IOException e) {
            logger.info("service is not available :" + host + ":" + port);
            return false;
        }
    }
}
