package com.weblyzard.api.domain.weblyzard;

import java.util.List;

import javax.xml.bind.JAXBException;
import javax.xml.bind.annotation.XmlAttribute;

/**
 * Data format used to return to the Web service client
 * 
 * @author Albert Weichselbraun <albert@weblyzard.com>
 *
 */
public class XmlDocument {

	@XmlAttribute(name = "content_id", required = true)
	public String content_id;
	@XmlAttribute(name = "xml_content", required = true)
	public String xml_content;
	public String nilsimsa;
	public List<Annotation> annotation;
	public String error;



	public XmlDocument() {
	}



	public XmlDocument(Document document, List<Annotation> annotation) throws JAXBException {
		content_id = document.id;
		nilsimsa = document.nilsimsa;
		this.annotation = annotation;
		xml_content = document.marshal();
	}
}
