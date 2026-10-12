package com.apiece.springboot_sns_sample.domain.recommendation;

import com.apiece.springboot_sns_sample.domain.post.Post;
import java.util.List;

public record RecommendationPage(List<Post> posts, String nextCursor, String mode) {
}
