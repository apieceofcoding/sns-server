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

    // 본문은 보내지 않습니다. 추천 worker가 글 ID로 원본을 읽고, 버전으로 최신 여부를 확인해요.
    public static Map<String,Object> post(long id,long version) {return event("post.updated",id,version);}

    public static Map<String,Object> deleted(long id,long version) {return event("post.deleted",id,version);}

    private static Map<String,Object> event(String kind,long id,long version) {
        return Map.of("event_id",UUID.randomUUID().toString(),"kind",kind,
            "post_id",id,"version",version,"occurred_at",Instant.now().toString());
    }
}
