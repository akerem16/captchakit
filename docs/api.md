# API Reference

## Manager

::: captchakit.manager.CaptchaManager

## Challenges

::: captchakit.challenges.base.Challenge
::: captchakit.challenges.base.ChallengeSpec
::: captchakit.challenges.base.ChallengeFactory

::: captchakit.challenges.text.TextChallengeFactory
::: captchakit.challenges.math.MathChallengeFactory
::: captchakit.challenges.grid.EmojiGridChallengeFactory
::: captchakit.challenges.word.WordChallengeFactory

## Renderers

::: captchakit.renderers.base.Renderer
::: captchakit.renderers.image.ImageRenderer
::: captchakit.renderers.svg.SVGRenderer
::: captchakit.renderers.theme.Theme
::: captchakit.renderers.audio.AudioRenderer

## Storage

::: captchakit.storage.base.Storage
::: captchakit.storage.memory.MemoryStorage
::: captchakit.storage.redis.RedisStorage
::: captchakit.storage.postgres.PostgresStorage

## Rate limiting

::: captchakit.ratelimit.RateLimiter
::: captchakit.ratelimit.NoOpRateLimiter
::: captchakit.ratelimit.TokenBucketRateLimiter

## i18n

::: captchakit.i18n.PromptTranslator
::: captchakit.i18n.DefaultTranslator

## Metrics

::: captchakit.metrics.MetricsSink
::: captchakit.metrics.NoOpMetrics

## Errors

::: captchakit.errors
