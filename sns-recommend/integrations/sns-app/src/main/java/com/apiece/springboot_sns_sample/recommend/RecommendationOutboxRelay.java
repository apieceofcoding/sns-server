package com.apiece.springboot_sns_sample.recommend;

import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClient;

@Component
public class RecommendationOutboxRelay {
    private final JdbcTemplate jdbc;
    private final RestClient client;
    public RecommendationOutboxRelay(JdbcTemplate jdbc,
        @Value("${recommend.url:http://localhost:8001}") String url,
        @Value("${recommend.token:course-local-token}") String token) {
        this.jdbc=jdbc;
        var factory=new org.springframework.http.client.JdkClientHttpRequestFactory(
            java.net.http.HttpClient.newBuilder().connectTimeout(java.time.Duration.ofSeconds(1)).build());
        factory.setReadTimeout(java.time.Duration.ofSeconds(3));
        this.client=RestClient.builder().baseUrl(url).requestFactory(factory)
            .defaultHeader("X-Internal-Token",token).build();
    }

    @Scheduled(fixedDelay=1000)
    @Transactional
    public void deliver() {
        var rows=jdbc.queryForList("select id,event::text as event from recommendation_outbox " +
            "where delivered_at is null order by created_at for update skip locked limit 20");
        for (var row:rows) {
            client.post().uri("/internal/events").contentType(MediaType.APPLICATION_JSON)
                .body(row.get("event").toString()).retrieve().toBodilessEntity();
            jdbc.update("update recommendation_outbox set delivered_at=now() where id=?",(UUID)row.get("id"));
        }
    }
}
