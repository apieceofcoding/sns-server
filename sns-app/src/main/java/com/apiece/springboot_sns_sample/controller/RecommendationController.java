package com.apiece.springboot_sns_sample.controller;

import com.apiece.springboot_sns_sample.api.post.PostResponse;
import com.apiece.springboot_sns_sample.config.auth.AuthUser;
import com.apiece.springboot_sns_sample.controller.dto.RecommendationResponse;
import com.apiece.springboot_sns_sample.domain.post.PostService;
import com.apiece.springboot_sns_sample.domain.recommendation.RecommendationService;
import com.apiece.springboot_sns_sample.domain.user.User;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequiredArgsConstructor
public class RecommendationController {

    private final RecommendationService recommendations;
    private final PostService posts;

    @GetMapping("/api/v1/recommendations")
    public ResponseEntity<RecommendationResponse> get(@AuthUser User user,
            @RequestParam(required = false) String cursor,
            @RequestParam(defaultValue = "20") int limit) {
        if (user == null) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);
        var page = recommendations.get(user.getId(), limit, cursor);
        var result = posts.enrichWithUserContext(page.posts(), user).stream().map(PostResponse::from).toList();
        return ResponseEntity.ok(new RecommendationResponse(result, page.nextCursor(),
                page.nextCursor() != null, page.mode()));
    }
}
