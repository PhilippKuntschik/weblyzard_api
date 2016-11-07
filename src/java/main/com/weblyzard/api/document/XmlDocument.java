package com.weblyzard.api.document;

import java.util.List;

import javax.xml.bind.JAXBException;
import javax.xml.bind.annotation.XmlAttribute;

import com.weblyzard.api.document.Document;
import com.weblyzard.api.document.annotation.Annotation;

/**
 * Data format used to return to the Web service client
 * 
 * @author albert@weblyzard.com
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
		content_id = document.getId();
		nilsimsa = document.getNilsimsa();
		this.annotation = annotation;
		xml_content = Document.getXmlRepresentation(document);
	}
}
