package com.apiece.springboot_sns_sample.recommend;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Component
public class RecommendationOutbox {
    private final JdbcTemplate jdbc;
    private final ObjectMapper mapper;
    public RecommendationOutbox(JdbcTemplate jdbc) {this.jdbc=jdbc;this.mapper=new ObjectMapper();}

    @Transactional(propagation=Propagation.MANDATORY)
    public void append(Map<String,Object> event) {
        try {
            jdbc.update("insert into recommendation_outbox(id,event) values (? ,?::jsonb)",
                UUID.fromString(event.get("event_id").toString()),mapper.writeValueAsString(event));
        } catch (JsonProcessingException ex) {throw new IllegalArgumentException(ex);}
    }

    public static Map<String,Object> post(long id,long authorId,long version,String body) {
        return Map.of("event_id",UUID.randomUUID().toString(),"kind","post.updated",
            "post_id",id,"version",version,"occurred_at",Instant.now().toString(),
            "payload",Map.of("body",body,"author_id",authorId,"topic","unknown"));
    }
}
