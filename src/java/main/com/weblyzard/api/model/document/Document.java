package com.weblyzard.api.model.document;

import java.io.Serializable;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import javax.xml.bind.Unmarshaller;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAnyAttribute;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlRootElement;
import javax.xml.bind.annotation.adapters.XmlJavaTypeAdapter;
import javax.xml.namespace.QName;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.weblyzard.api.model.Lang;
import com.weblyzard.api.model.annotation.Annotation;
import com.weblyzard.api.serialize.json.DocumentHeaderDeserializer;
import com.weblyzard.api.serialize.xml.LangAdapter;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

/**
 * The {@link Document} and {@link Sentence} model classes used to represent documents.
 *
 * <p>
 * The {@link Document} class also supports arbitrary meta data which is stored in the <code>
 * header</code> instance variable.
 *
 * <p>
 * The static helper function {@link Document#toXml(Document)} and
 * {@link Document#fromXml(String)} translate between {@link Document} objects
 * and the corresponding XML representations.
 *
 * @author weichselbraun@weblyzard.com
 */
@Data
@Accessors(chain = true)
@NoArgsConstructor
@XmlRootElement(name = "page", namespace = Document.NS_WEBLYZARD)
@JsonIgnoreProperties(ignoreUnknown = true)
@XmlAccessorType(XmlAccessType.FIELD)
public class Document implements Serializable {

    private static final long serialVersionUID = 1L;
    public static final String NS_WEBLYZARD = "http://www.weblyzard.com/wl/2013#";
    public static final String NS_DUBLIN_CORE = "http://purl.org/dc/elements/1.1/";

    /** The Attribute used to encode document keywords */
    public static final QName WL_KEYWORD_ATTR = new QName(NS_DUBLIN_CORE, "subject");

    @XmlAttribute(name = "id", namespace = Document.NS_WEBLYZARD)
    private String id;

    @XmlAttribute(name = "format", namespace = Document.NS_DUBLIN_CORE)
    private String format;

    @JsonProperty("lang")
    @XmlAttribute(name = "lang", namespace = javax.xml.XMLConstants.XML_NS_URI)
    @XmlJavaTypeAdapter(LangAdapter.class)
    private Lang lang;

    @XmlAttribute(namespace = Document.NS_WEBLYZARD)
    private String nilsimsa;

    @JsonDeserialize(keyUsing = DocumentHeaderDeserializer.class)
    @XmlAnyAttribute
    private Map<QName, String> header = new HashMap<>();

    /** Elements used in the output (and input) */
    @JsonProperty("sentences")
    @XmlElement(name = "sentence", namespace = Document.NS_WEBLYZARD)
    private List<Sentence> sentences;

    /**
     * This field contains all annotations after titleAnnotations and bodyAnnotations have been
     * merged. (i.e. after the document's finalization)
     */
    @JsonProperty("annotations")
    @XmlElement(name = "annotation", namespace = Document.NS_WEBLYZARD)
    private List<Annotation> annotations;

    @Override
    public Object clone() throws CloneNotSupportedException {
        return super.clone();
    }

    /**
     * Converts a {@link Document} to the corresponding webLyzard XML representation
     *
     * @param document The {@link Document} object to convert.
     * @return An XML representation of the given {@link Document} object.
     * @throws JAXBException
     */
    public static String toXml(Document document) throws JAXBException {
        StringWriter stringWriter = new StringWriter();
        JAXBElement<Document> jaxbElement = new JAXBElement<>(
                new QName(Document.NS_WEBLYZARD, "page", "wl"), Document.class, document);
        JAXBContext jaxbContext = JAXBContext.newInstance(Document.class);
        Marshaller xmlMarshaller = jaxbContext.createMarshaller();
        xmlMarshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);
        xmlMarshaller.marshal(jaxbElement, stringWriter);
        return stringWriter.toString();
    }

    /**
     * Converts a webLyzard XML Document to a {@link Document}.
     *
     * @param xmlString The webLyzard XML document to unmarshall
     * @return The {@link Document} instance corresponding to the xmlString
     * @throws JAXBException
     */
    public static Document fromXml(String xmlString) throws JAXBException {
        JAXBContext jaxbContext = JAXBContext.newInstance(Document.class);
        Unmarshaller unmarshaller = jaxbContext.createUnmarshaller();
        StringReader reader = new StringReader(xmlString);
        return (Document) unmarshaller.unmarshal(reader);
    }
}