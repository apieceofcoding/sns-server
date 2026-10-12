package com.apiece.springboot_sns_sample.controller;

import com.apiece.springboot_sns_sample.config.auth.AuthUser;
import com.apiece.springboot_sns_sample.domain.post.PostService;
import com.apiece.springboot_sns_sample.domain.recommendation.RecommendationPage;
import com.apiece.springboot_sns_sample.domain.recommendation.RecommendationService;
import com.apiece.springboot_sns_sample.domain.user.User;
import org.junit.jupiter.api.Test;
import org.springframework.core.MethodParameter;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.bind.support.WebDataBinderFactory;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.method.support.ModelAndViewContainer;

import java.util.List;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class RecommendationControllerTest {

    @Test
    void usesAuthenticatedUserInsteadOfQueryUserId() throws Exception {
        var recommendations = mock(RecommendationService.class);
        var posts = mock(PostService.class);
        User user = User.create("reader", "");
        ReflectionTestUtils.setField(user, "id", 7L);
        when(recommendations.get(7, 20, null)).thenReturn(new RecommendationPage(List.of(), "next", "recommend"));
        when(posts.enrichWithUserContext(List.of(), user)).thenReturn(List.of());

        MockMvcBuilders.standaloneSetup(new RecommendationController(recommendations, posts))
                .setControllerAdvice(new RecommendationExceptionHandler())
                .setCustomArgumentResolvers(resolver(user)).build()
                .perform(get("/api/v1/recommendations?userId=999"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.mode").value("recommend"))
                .andExpect(jsonPath("$.nextCursor").value("next"))
                .andExpect(jsonPath("$.hasMore").value(true));
        verify(recommendations).get(7, 20, null);
    }

    @Test
    void rejectsMissingUserBeforeCallingRecommendation() throws Exception {
        var recommendations = mock(RecommendationService.class);
        MockMvcBuilders.standaloneSetup(new RecommendationController(recommendations, mock(PostService.class)))
                .setControllerAdvice(new RecommendationExceptionHandler())
                .setCustomArgumentResolvers(resolver(null)).build()
                .perform(get("/api/v1/recommendations"))
                .andExpect(status().isUnauthorized());
        verifyNoInteractions(recommendations);
    }

    @Test
    void returnsExpiredCursorWithoutAnErrorDispatch() throws Exception {
        var recommendations = mock(RecommendationService.class);
        User user = User.create("reader", "");
        ReflectionTestUtils.setField(user, "id", 7L);
        when(recommendations.get(7, 20, "old")).thenThrow(new org.springframework.web.server.ResponseStatusException(
                org.springframework.http.HttpStatus.GONE, "추천 세션을 새로 시작하세요"));
        MockMvcBuilders.standaloneSetup(new RecommendationController(recommendations, mock(PostService.class)))
                .setControllerAdvice(new RecommendationExceptionHandler())
                .setCustomArgumentResolvers(resolver(user)).build()
                .perform(get("/api/v1/recommendations?cursor=old"))
                .andExpect(status().isGone())
                .andExpect(jsonPath("$.status").value(410));
    }

    private HandlerMethodArgumentResolver resolver(User user) {
        return new HandlerMethodArgumentResolver() {
            public boolean supportsParameter(MethodParameter parameter) {
                return parameter.hasParameterAnnotation(AuthUser.class);
            }
            public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer container,
                                          NativeWebRequest request, WebDataBinderFactory factory) {
                return user;
            }
        };
    }
}
