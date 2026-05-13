package com.hades.dataflow.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class NodeSchemaDTO {
    private String type;
    private String label;
    private String category;
    private String icon;
    private List<FieldDef> fields;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FieldDef {
        private String key;
        private String label;
        private String type;
        private String placeholder;
        private boolean required;
        private boolean autoFilled;
      private List<String> options;
        private String widget;
        private WidgetConfig widgetConfig;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
  public static class WidgetConfig {
        private String keyPlaceholder;
        private String valuePlaceholder;
        private String valueType;
      private List<String> valueOptions;
    }
}
