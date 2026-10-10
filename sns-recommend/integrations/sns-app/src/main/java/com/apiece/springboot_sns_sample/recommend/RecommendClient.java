package com.apiece.springboot_sns_sample.recommend;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.net.http.HttpClient;
import java.time.Duration;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class RecommendClient {
    private final RestClient client;

    public RecommendClient(@Value("${recommend.url:http://localhost:8001}") String url,
                           @Value("${recommend.token:course-local-token}") String token) {
        var http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(1)).build();
        var factory = new JdkClientHttpRequestFactory(http);
        factory.setReadTimeout(Duration.ofSeconds(2));
        client = RestClient.builder().baseUrl(url).requestFactory(factory)
            .defaultHeader("X-Internal-Token", token).build();
    }

    public Feed get(long userId, int limit, String cursor) {
        return client.get().uri(builder -> {
            builder.path("/internal/feeds/{id}").queryParam("limit", limit);
            if (cursor != null) builder.queryParam("cursor", cursor);
            return builder.build(userId);
        }).retrieve().body(Feed.class);
    }

    public record Feed(boolean ready, @JsonProperty("post_ids") List<Long> postIds,
                       @JsonProperty("next_cursor") String nextCursor) {}
}
