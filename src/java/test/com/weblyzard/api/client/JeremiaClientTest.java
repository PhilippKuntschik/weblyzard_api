package com.weblyzard.api.client;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assume.assumeTrue;

import javax.ws.rs.ClientErrorException;
import javax.xml.bind.JAXBException;

import org.junit.Before;
import org.junit.Test;

import com.weblyzard.api.document.Document;

public class JeremiaClientTest extends TestClientBase{
	
	private JeremiaClient jeremiaClient; 
	
	@Before
	public void before() {
		jeremiaClient = new JeremiaClient(); 
	}

	@Test
	public void testSubmitDocument() throws ClientErrorException, JAXBException {
		assumeTrue(weblyzardServiceAvailable(jeremiaClient));
		Document request = new Document(
				"Fast Track's Karen Bowerman asks what the changes in penguin population could mean for the rest of us in the event of climate change.");
		request.setLang("en");
		Document response = jeremiaClient.submitDocument(request);
		assertNotNull(response);
	}
}
