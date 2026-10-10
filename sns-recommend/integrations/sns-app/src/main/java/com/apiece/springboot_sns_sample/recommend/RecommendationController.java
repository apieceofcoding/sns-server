package com.apiece.springboot_sns_sample.recommend;

import com.apiece.springboot_sns_sample.api.post.PostResponse;
import com.apiece.springboot_sns_sample.config.auth.AuthUser;
import com.apiece.springboot_sns_sample.domain.post.Post;
import com.apiece.springboot_sns_sample.domain.post.PostRepository;
import com.apiece.springboot_sns_sample.domain.post.PostService;
import com.apiece.springboot_sns_sample.domain.user.User;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class RecommendationController {
    private final RecommendClient client;
    private final PostRepository posts;
    private final PostService service;
    private final RecommendationPostRepository latest;

    public RecommendationController(RecommendClient client, PostRepository posts,
                                    PostService service, RecommendationPostRepository latest) {
        this.client=client; this.posts=posts; this.service=service; this.latest=latest;
    }

    @GetMapping("/api/v1/recommendations")
    public Page feed(@AuthUser User user, @RequestParam(required=false) String cursor,
                     @RequestParam(defaultValue="20") int limit) {
        if (limit<1 || limit>50) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
        if (cursor!=null && cursor.startsWith("latest:")) {
            try { return fallback(user, Long.parseLong(cursor.substring(7)),limit); }
            catch (NumberFormatException ex) { throw new ResponseStatusException(HttpStatus.BAD_REQUEST); }
        }
        RecommendClient.Feed feed;
        try { feed=client.get(user.getId(),limit,cursor); }
        catch (RestClientException ex) {
            if (cursor!=null) throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                "추천 세션을 새로 시작하세요");
            return fallback(user,Long.MAX_VALUE,limit);
        }
        if (feed==null || !feed.ready()) return fallback(user,Long.MAX_VALUE,limit);
        var map=posts.findAllByIdInAndDeletedAtIsNull(feed.postIds()).stream()
            .collect(Collectors.toMap(Post::getId,Function.identity()));
        var ordered=feed.postIds().stream().map(map::get).filter(Objects::nonNull).toList();
        return response(user,ordered,feed.nextCursor(),"recommend");
    }

    private Page fallback(User user,long before,int limit) {
        var page=latest.latest(before,PageRequest.of(0,limit+1));
        var selected=page.stream().limit(limit).toList();
        var next=page.size()>limit ? "latest:"+selected.getLast().getId() : null;
        return response(user,selected,next,"latest");
    }

    private Page response(User user,List<Post> ordered,String cursor,String mode) {
        var result=service.enrichWithUserContext(ordered,user).stream().map(PostResponse::from).toList();
        return new Page(result,cursor,cursor!=null,mode);
    }

    public record Page(List<PostResponse> posts,String nextCursor,boolean hasMore,String mode) {}
}
