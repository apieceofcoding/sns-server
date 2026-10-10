package com.apiece.springboot_sns_sample.recommend;

import com.apiece.springboot_sns_sample.domain.post.Post;
import java.util.List;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.Repository;
import org.springframework.data.repository.query.Param;

public interface RecommendationPostRepository extends Repository<Post, Long> {
    @Query("select p from Post p where p.deletedAt is null and p.id < :before order by p.id desc")
    List<Post> latest(@Param("before") long before, Pageable pageable);
}
