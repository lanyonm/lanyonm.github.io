---
layout: post
title: "Spring 4 and MyBatis Java Config"
description: "An example of MyBatis-Spring configuration with Java Config with Spring 4 and MyBatis 3.2.7"
category: articles
tags: [development, H2, java, MyBatis, software, Spring]
comments: true
---

# TL;DR
With the Java Config enhancements in Spring 4, you no longer need xml to configure MyBatis for your Spring application. Using the [`@MapperScan`](https://mybatis.github.io/spring/apidocs/reference/org/mybatis/spring/annotation/MapperScan.html) annotation provided by the [mybatis-spring](http://mybatis.github.io/spring/) library, you can perform a package-level scan for MyBatis domain mappers. When combined with Servlet 3+, you can configure and run your application without any XML (aside from the MyBatis query definitions). This post is a long overdue follow up to a [previous post]({% post_url 2013-01-19-mybatis-spring-java-config-contribution %}) about my contribution to this code.

<div class="center spring-mybatis">
  <img src="https://spring.io/img/spring-by-pivotal.png" alt="Spring Framework" />
  <span>+</span>
  <img src="https://mybatis.github.io/images/mybatis-logo.png" alt="MyBatis" />
</div>

***Please note***: The examples shown here work with Spring 4.0.6 and 4.2.4. Check the master branch on GitHub for updates to the version of Spring compatible with these examples.

# A Java Config Appetizer
There is a lot of conflicting information out there for those searching for how to implement Spring's Java Config. Be sure to check the version of Spring used in the example because it may not match your target version. This example uses Spring Framework 4.0.6 and MyBatis 3.2.7. As not to get into the weeds of Java Config for a Spring MCV application, we'll cover just the pertinent parts to integrating MyBatis with Java Config.

Have a look at the file structure below. The [`AppInitializer`](https://github.com/lanyonm/playground/blob/28c34b185ca796e1e1b18d4134d1a147c6996b97/src/main/java/org/lanyonm/playground/config/AppInitializer.java) with its `AbstractAnnotationConfigDispatcherServletInitializer` super class is where life begins for the application. The `getRootConfigClasses()` method returns the `DataConfg` class amongst others not pictured below.

File structure:

    - src/main
        - java/org/lanyonm/playground
            - config
                * AppInitializer.java
                * DataConfig.java
            - domain
                * User.java
            - persistence
                * UserMapper.java
        - resources/org/lanyonm/playground
            - persistence
                * UserMapper.xml
    * pom.xml

It's my preference to put all the `@Component` or `@Configuration` classes into the config package so it's easy to locate where the application components are configured.

# The Key Files
There are four main files in this example. The first and most important is `DataConfig.java` because it's where the `@MapperScan` annotation is used. On line 2, you see the package where the MyBatis mappers reside. The three `@Bean` annotated methods provide the Java Config equivalent to what you would typically see in xml configuration for MyBatis. In this case a `SimpleDriverDataSource` is used in place of a full-blown DataSource and specifies an in-memory H2 database. In future iterations of this application I will show how to use Spring's Profiles to specify different DataSource implementations depending on the environment.

org.lanyonm.playground.config.[`DataConfig.java`](https://github.com/lanyonm/playground/blob/28c34b185ca796e1e1b18d4134d1a147c6996b97/src/main/java/org/lanyonm/playground/config/DataConfig.java):
{% highlight java linenos %}
@Configuration
@MapperScan("org.lanyonm.playground.persistence")
public class DataConfig {

    @Bean
    public DataSource dataSource() {
        SimpleDriverDataSource dataSource = new SimpleDriverDataSource();
        dataSource.setDriverClass(org.h2.Driver.class);
        dataSource.setUsername("sa");
        dataSource.setUrl("jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE");
        dataSource.setPassword("");

        // create a table and populate some data
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
        System.out.println("Creating tables");
        jdbcTemplate.execute("drop table users if exists");
        jdbcTemplate.execute("create table users(id serial, firstName varchar(255), lastName varchar(255), email varchar(255))");
        jdbcTemplate.update("INSERT INTO users(firstName, lastName, email) values (?,?,?)", "Mike", "Lanyon", "lanyonm@gmail.com");

        return dataSource;
    }

    @Bean
    public DataSourceTransactionManager transactionManager() {
        return new DataSourceTransactionManager(dataSource());
    }

    @Bean
    public SqlSessionFactoryBean sqlSessionFactory() throws Exception {
        SqlSessionFactoryBean sessionFactory = new SqlSessionFactoryBean();
        sessionFactory.setDataSource(dataSource());
        sessionFactory.setTypeAliasesPackage("org.lanyonm.playground.domain");
        return sessionFactory;
    }
}
{% endhighlight %}

The second important piece of `DataConfig` is on line 32 where we set the package containing the domain objects that will be available as types in the MyBatis xml files. Returning Java objects from SQL queries is why we go to all this ORM trouble after all.

The User domain object is really just a simple POJO. I've omitted the getters and setters for brevity.

org.lanyonm.playground.domain.[`User.java`](https://github.com/lanyonm/playground/blob/28c34b185ca796e1e1b18d4134d1a147c6996b97/src/main/java/org/lanyonm/playground/domain/User.java):
{% highlight java linenos %}
public class User implements Serializable {

    private static final long serialVersionUID = 1L;
    private long id;
    private String firstName;
    private String lastName;
    private String email;

    // getters and setters

}
{% endhighlight %}

MyBatis Mapper classes are simple interfaces with method definitions that match with a sql statement defined in the corresponding mapper xml. It is possible to write simple sql statements in annotations instead of defining the sql in xml, but the syntax becomes cumbersome quickly and doesn't allow for complex queries.

org.lanyonm.playground.persistence.[`UserMapper.java`](https://github.com/lanyonm/playground/blob/28c34b185ca796e1e1b18d4134d1a147c6996b97/src/main/java/org/lanyonm/playground/persistence/UserMapper.java):
{% highlight java linenos %}
public interface UserMapper {
    /**
     * @return all the users
     */
    public List<User> getAllUsers();
    /**
     * @param user
     * @return the number of rows affected
     */
    public int insertUser(User user);
    /**
     * @param user
     * @return the number of rows affected
     */
    public int updateUser(User user);
}
{% endhighlight %}

I haven't done anything special with the MyBatis xml, just a few simple statements.

org.lanyonm.playground.persistence.[`UserMapper.xml`](https://github.com/lanyonm/playground/blob/28c34b185ca796e1e1b18d4134d1a147c6996b97/src/main/resources/org/lanyonm/playground/persistence/UserMapper.xml):
{% highlight xml linenos %}
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="org.lanyonm.playground.persistence.UserMapper">
    <cache />

    <select id="getAllUsers" resultType="User">
        SELECT id, firstName, lastName, email FROM users
    </select>

    <insert id="insertUser" parameterType="User">
        INSERT INTO users (firstName, lastName, email)
        VALUES (#{firstName}, #{lastName}, #{email})
    </insert>

    <update id="updateUser" parameterType="User">
        UPDATE users SET
            firstName = #{firstName},
            lastName = #{lastName},
            email = #{email}
        WHERE ID = #{id}
    </update>
</mapper>
{% endhighlight %}

That's pretty much all there is to it. If you find something I left out, please let me know. The full source code for this example resides in the [playground](https://github.com/lanyonm/playground/tree/28c34b185ca796e1e1b18d4134d1a147c6996b97) repo on GitHub.
