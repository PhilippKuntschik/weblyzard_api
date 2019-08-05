package com.weblyzard.api.model.joel;

import java.io.Serializable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

/**
 * A {@link Cluster} with the corresponding {@link Topic}s as returned by the Joel clustering service.
 * 
 * @author Norman Süsstrunk
 */
@Data
@Accessors(chain = true)
@NoArgsConstructor
@AllArgsConstructor
public class ClusterResult implements Serializable {

    private static final long serialVersionUID = 1L;

    private Topic topic;
    private Cluster cluster;
}
