package com.weblyzard.api;

import java.io.IOException;

import javax.xml.bind.JAXBException;

import org.apache.http.auth.AuthenticationException;
import org.apache.http.client.ClientProtocolException;

import com.weblyzard.api.domain.joseph.ClassifyRequest;
import com.weblyzard.api.domain.joseph.ClassifyResponse;

/**
 * TODO: test this with the current version of joseph. the deployed version
 * cannot parse the incoming document class.
 * 
 * @author phil
 *
 */
public class JosephConnectorTest {

	JosephConnector connector = new JosephConnector();

	String profile = "yourProfilename";
	
	/*
	 * TODO: Tests have been deactivated since there is no dummy webservice for public availability.
	 */

//	@Test
//	public void testClassify() throws AuthenticationException, ClientProtocolException, IOException, JAXBException {
//		ClassifyResponse[] responses = classify(profile, new ClassifyRequest());
//		return;
//	}
//
//
//
//	@Test
//	public void testClassifyExtended()
//			throws AuthenticationException, ClientProtocolException, IOException, JAXBException {
//		ClassifyResponse[] responses = classifyExtended(profile, new ClassifyRequest());
//		return;
//	}



	private ClassifyResponse[] classify(String profile, ClassifyRequest data)
			throws AuthenticationException, ClientProtocolException, IOException, JAXBException {
		return connector.callClassify(profile, data);
	}



	private ClassifyResponse[] classifyExtended(String profile, ClassifyRequest data)
			throws AuthenticationException, ClientProtocolException, IOException, JAXBException {
		return connector.callClassifyExtended(profile, data);
	}
}