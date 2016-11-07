package com.weblyzard.api.client.joel;

import java.util.List;

import javax.ws.rs.ClientErrorException;
import javax.ws.rs.client.Entity;
import javax.ws.rs.core.GenericType;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.xml.bind.JAXBException;

import com.weblyzard.api.client.BasicClient;
import com.weblyzard.api.document.Document;

/**
 * 
 * @author philipp.kuntschik@htwchur.ch, norman.suesstrunk@htwchur.ch
 *
 */
public class JoelClient extends BasicClient {

	private static final String ADDDOCUMENTS_SERVICE_URL = "/joel/rest/addDocuments";
	private static final String CLUSTER_DOCUMENT_SERVICEURL = "/joel/rest/cluster";
	private static final String FLUSH_DOCUMENT_SERVICE_URL = "/joel/rest/flush";


	/**
	 * @see BasicClient
	 */
	public JoelClient() {
		super();
	}

	public Response addDocuments(List<Document> documents) throws ClientErrorException, JAXBException {
		Response response = super.target.path(ADDDOCUMENTS_SERVICE_URL).request(MediaType.APPLICATION_JSON_TYPE)
				.post(Entity.json(documents));
		super.checkResponseStatus(response);
		response.close(); 
		return response;
	}


	public Response flush() throws ClientErrorException {
		Response response = super.target.path(FLUSH_DOCUMENT_SERVICE_URL).request(MediaType.APPLICATION_JSON_TYPE).get();
		super.checkResponseStatus(response);
		response.close();
		return response;
	}



	public List<ClusterResult> cluster() throws ClientErrorException {
		Response response = super.target.path(CLUSTER_DOCUMENT_SERVICEURL).request(MediaType.APPLICATION_JSON_TYPE).get();
		super.checkResponseStatus(response);
		List<ClusterResult> clusterResults = response.readEntity(new GenericType<List<ClusterResult>>() {});
		response.close();
		return clusterResults;
	}
}