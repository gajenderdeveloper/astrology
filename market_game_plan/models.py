from django.db import models

# Create your models here.


class PreMarketActivities(models.Model):

    brain_dump= models.TextField('Brain dump ( write anything on your mind about trading, money, fear greed or distraction)')
    meditation = models.CharField('meditation', max_length=50, null=False, blank=False,
                        choices=[
                            ('Done', 'Done'),
                            ('Not Done', 'Not Done'),
                            ('Did not get time', 'Did not get time'), 
                            ]
                        )
    action = models.TextField()
    feel_now = models.CharField('do I feel like I need to win today?',max_length=50,null=False, 
                        blank=False,
                        choices=[
                            ('Yes', 'Yes'),
                            ('No', 'No')
                            ]
                        )
    over_confident = models.CharField('do I feel like I need to win today?',max_length=50,
                            null=False, 
                            blank=False,
                            choices=[
                                ('Yes', 'Yes'),
                                ('No', 'No'),
                                ('Not Applicable', 'Not Applicable')
                                ]
                            )
    market_context= models.TextField()
    economic_calender= models.TextField()
    daily = models.CharField(null=False, max_length=50,
                                blank=False,
                                choices=[
                                    ('BULLISH', 'BULLISH'),
                                    ('BEARISH', 'BEARISH'),
                                    ('RANGEBOUND', 'RANGEBOUND')
                                    ]
                                )
    weekly = models.CharField(null=False, max_length=50,
                                    blank=False,
                                    choices=[
                                        ('BULLISH', 'BULLISH'),
                                        ('BEARISH', 'BEARISH'),
                                        ('RANGEBOUND', 'RANGEBOUND')
                                        ]
                                    )
    sleep = models.CharField(null=False, max_length=50,
                                        blank=False,
                                        choices=[
                                            ('Full', 'BULFullLISH'),
                                            ('Half', 'Half'),
                                            ('Not slept', 'Not slept')
                                            ]
                                        )
    mood = models.CharField(null=False, max_length=50,
                                        blank=False,
                                        choices=[
                                            ('Good', 'Good'),
                                            ('Verygood', 'Verygood'),
                                            ('Feeling Positive', 'Not slept'),
                                            ('Feeling over confident', 'Feeling over confident')
                                            ]
                                        )
    

    emotional_strategy= models.TextField('emotional strategy')
    word_for_today = models.CharField(null=False, max_length=50,
                                            blank=False,
                                            choices=[
                                                ('planned', 'planned'),
                                                ('structured', 'structured'),
                                                ('programmerd', 'programmerd'),
                                                ('practiced', 'practiced'),
                                                ('displicine', 'displicine')
                                                ]
                                            )
    confidence_level = models.IntegerField(
                            choices=[(i, str(i)) for i in range(1, 11)],
                            default=5,
                            help_text="Select a rating between 1 and 10"
                        )
    bell_curve = models.TextField()
    position_sizing_plan = models.TextField()
    lession_from_prev_session = models.TextField()
    gratitudes_mention = models.TextField('5 gratitudes mention in your life',default="")


    created_at = models.DateField(auto_now=True,unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.feel_now

    class Meta:
        """docstring for meta"""
        ordering = ('id',)
        verbose_name_plural = "Pre Market Activities"      


class RulesAndComplience(models.Model):
    
    trade_before = models.CharField('I will not take trade before?', max_length=50, null=False, 
                        blank=False,
                        choices=[
                            ('one', 'one'),
                            ('two', 'two'),
                            ('three', 'three'),
                            
                            ]
                        )
    consequtive_losses = models.TextField('I will stop after 2 consequtive losses')
    take_only  = models.CharField('I will only take ',max_length=50,null=False, 
                        blank=False,
                        choices=[
                            ('ORB', 'ORB'),
                            ('RSI SETUP', 'RSI SETUP'),
                            ('reversal', 'reversal')
                            ]
                        )
    belief_throw = models.TextField('one belief to throw')
    belief_keep = models.TextField('one belief to keep ')

   

    created_at = models.DateField(auto_now=True,unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.trade_before

    class Meta:
        """docstring for meta"""
        ordering = ('id',)


class PostmarketActivities(models.Model):
    
    best_trade = models.TextField('BEST trade why?')
    worst_trade = models.TextField('worst trade why?')
    missed_trade = models.TextField('missed trade')

    trade_journals  = models.CharField(max_length=50,null=False, 
                        blank=False,
                        choices=[
                            ('Done', 'Done'),
                            ('Not Done', 'Not Done'),
                            ]
                        )
    action_yesterday  = models.CharField('action taken today for yesterday lession?',max_length=50,
                                       null=False, 
                            blank=False,
                            choices=[
                                ('Yes', 'Yes'),
                                ('No', 'No'),
                                ]
                            )
    
    what_great_today = models.TextField('what did I did great today?')
    reinfocement_lession = models.TextField('reinfocement lession')
    follow_bellcurve_today  = models.CharField('did I follow bellcurve today',max_length=50,
                                           null=False, 
                                blank=False,
                                choices=[
                                    ('Yes', 'Yes'),
                                    ('No', 'No'),
                                    ]
                                )
    emotions_showed_up_today  = models.CharField('what emotions showed up today?',max_length=50,
                                               null=False, 
                                    blank=False,
                                    choices=[
                                        ('calm', 'calm'),
                                        ('impatience', 'impatience'),
                                        ('greedy', 'greedy'),
                                        ('fearful', 'fearful'),
                                        ]
                                    )
    better_tomorrow = models.TextField('one thing I do better tomorrow?')
    goal_expectation = models.TextField('goal/expectation')
    created_at = models.DateField(auto_now=True,unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.trade_journals

    class Meta:
        """docstring for meta"""
        ordering = ('id',)


class Discipline(models.Model):
    
    emotions_today = models.TextField('what emotions showed up today?')
    discpline_today  = models.CharField('was it discpline today?',max_length=50,null=False, 
                        blank=False,
                        choices=[
                            ('yes', 'yes'),
                            ('no', 'no'),
                            ]
                        )
    
    created_at = models.DateField(auto_now=True,unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.discpline_today

    class Meta:
        """docstring for meta"""
        ordering = ('id',)

class TradeJournal(models.Model):

    symbol  = models.CharField(max_length=50,null=False, blank=False)
    created_at = models.DateTimeField(auto_now=True)
    execution_control = models.TextField('clear setup/trading plan followed')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.symbol

    class Meta:
        """docstring for meta"""
        ordering = ('id',)